from models.model import Model
from tensorflow.keras import Sequential, layers
from tensorflow.keras.optimizers import RMSprop, Adam

class BasicModel(Model):
    def _define_model(self, input_shape, categories_count):
        # Initialize the sequential model
        self.model = Sequential([
            # Input layer with rescaling to normalize pixel values to [0,1]
            layers.Rescaling(1./255, input_shape=input_shape),
            
            # First convolutional block
            layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            
            # Second convolutional block
            layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            layers.Dropout(0.25),
            
            # Third convolutional block
            layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            layers.BatchNormalization(),
            layers.MaxPooling2D((2, 2)),
            
            # Global Average Pooling instead of Flatten
            layers.GlobalAveragePooling2D(),
            layers.Dropout(0.5),
            
            # Fully connected layers
            layers.Dense(64, activation='relu'),
            layers.Dense(categories_count, activation='softmax')
        ])
    
    def _compile_model(self):
        # Compile the model with categorical crossentropy loss and RMSprop optimizer
        self.model.compile(
            optimizer=RMSprop(learning_rate=0.001),
            loss='categorical_crossentropy',
            metrics=['accuracy']
        )
